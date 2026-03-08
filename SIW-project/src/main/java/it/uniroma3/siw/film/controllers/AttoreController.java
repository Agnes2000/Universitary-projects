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

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import it.uniroma3.siw.film.controllers.components.validators.AttoreValidator;
import it.uniroma3.siw.film.model.Attore;
import it.uniroma3.siw.film.services.AttoreService;
import it.uniroma3.siw.film.utils.FileUploadUtil;

@Slf4j
@Controller
@RequiredArgsConstructor
public class AttoreController {

    private final AttoreService attoreService;
    private final AttoreValidator attoreValidator;

    @GetMapping("/admin/attori")
    public String getAttori(Model model){
        log.info("Richiesta GET /admin/attori");
        model.addAttribute("attori", this.attoreService.getAttori());
        return "admin/attori";
    }

    @GetMapping("/admin/attori/create")
    public String newAttore(Model model){
        log.info("Richiesta GET /admin/attori");
        model.addAttribute("attore", new Attore());
        return "admin/attoreForm";
    }

    @PostMapping("/admin/attori/create")
    public String saveAttore(@Valid @ModelAttribute Attore attore, @RequestParam("image") MultipartFile multipartFile, BindingResult bindingResult, Model model) throws IOException {
        log.info("Richiesta POST /admin/attori");
        this.attoreValidator.validate(attore, bindingResult);

        if(!bindingResult.hasErrors()) {
            log.info("Parametri inseriti Corretti");
            String fileName = StringUtils.cleanPath(multipartFile.getOriginalFilename());
            attore.setUrlImg(fileName);
            this.attoreService.salvaAttore(attore);
            String uploadDir = "attori-img/";
            FileUploadUtil.saveFile(uploadDir, fileName, multipartFile);
            model.addAttribute("attori", this.attoreService.getAttori());
            return "admin/attori";
        }
        log.info("Parametri inseriti non Validi");
        return "admin/attoreForm";
    }

    @GetMapping("/admin/attori/{id}/delete")
    public String deleteAttore(@PathVariable Long id){
        log.info("Richiesta GET /admin/attori" + id + "/delete");
        this.attoreService.cancellaAttore(id);
        return "forward:/admin/attori";
    }

    @GetMapping("/admin/attori/{id}/update")
    public String modificaAttore(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /admin/attori/" + id + "/update");
        model.addAttribute("attore", this.attoreService.getAttore(id));
        return "admin/attoreForm";
    }
    
}
