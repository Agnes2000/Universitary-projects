package it.uniroma3.siw.film.controllers;

import java.io.IOException;

import javax.validation.Valid;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.StringUtils;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import it.uniroma3.siw.film.controllers.components.validators.RegistaValidator;
import it.uniroma3.siw.film.model.Regista;
import it.uniroma3.siw.film.services.RegistaService;
import it.uniroma3.siw.film.utils.FileUploadUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequiredArgsConstructor
public class RegistaController {

    private final RegistaService registaService;
    private final RegistaValidator registaValidator;
    
    @GetMapping("/admin/registi")
    public String ottieniRegisti(Model model){
        log.info("Richiesta GET /admin/registi");
        model.addAttribute("registi", this.registaService.getRegisti());
        return "admin/registi";
    }

    @PostMapping("/admin/registi")
    public String salvaRegista(@Valid @ModelAttribute Regista regista, BindingResult bindingResult, @RequestParam("image") MultipartFile multipartFile, Model model) throws IOException {
        log.info("Richiesta POST /admin/registi");
        this.registaValidator.validate(regista, bindingResult);

        if(!bindingResult.hasErrors()) {
            log.info("Parametri inseriti Corretti");
            String fileName = StringUtils.cleanPath(multipartFile.getOriginalFilename());
            regista.setUrlImg(fileName);
            this.registaService.salvaRegista(regista);
            String uploadDir = "registi-img/";
            FileUploadUtil.saveFile(uploadDir, fileName, multipartFile);
            model.addAttribute("registi", this.registaService.getRegisti());
            return "admin/registi";
        }

        log.info("Parametri inseriti non Validi");
        return "admin/registaForm";
    }

    @GetMapping("/admin/registi/create")
    public String aggiungiRegista(Model model){
        log.info("Richiesta GET /admin/registi/create");
        model.addAttribute("regista", new Regista());
        return "admin/registaForm";
    }

    @GetMapping("/admin/registi/{id}/delete")
    public String cancellaRegista(@PathVariable Long id){
        log.info("Richiesta GET /admin/registi" + id + "/delete");
        this.registaService.cancellaRegista(id);
        return "forward:/admin/registi";
    }

    @GetMapping("/admin/registi/{id}/update")
    public String modificaRegista(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /admin/registi/" + id + "/update");
        model.addAttribute("regista", this.registaService.getRegista(id));
        return "admin/registaForm";
    }

}
