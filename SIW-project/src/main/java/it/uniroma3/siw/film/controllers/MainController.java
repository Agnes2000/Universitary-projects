package it.uniroma3.siw.film.controllers;

import java.time.LocalDate;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import it.uniroma3.siw.film.controllers.components.UserDetailsComponent;
import it.uniroma3.siw.film.services.FilmService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequiredArgsConstructor
public class MainController {

    private final UserDetailsComponent userDetailsComponent;
    private final FilmService filmService;

    @GetMapping(value = { "/", "/index" })
    public String index(Model model) {
        log.info("Richiesta GET /index");
        model.addAttribute("films", this.filmService.getTop5Film((short) LocalDate.now().getYear()));
        return "index";
    }

    @GetMapping("/profilo")
    public String mostraProfilo(Model model) {
        model.addAttribute("utente", this.userDetailsComponent.getUtenteAutenticato());
        return "profilo";
    }

    @GetMapping("/home")
    public String homeUtente(Model model) {
        log.info("Richiesta GET /home");
        model.addAttribute("films", this.filmService.getFilms());
        return "home";
    }

    @GetMapping("/admin/home")
    public String getAdminHome() {
        log.info("Richiesta GET /admin/home");
        return "admin/home";
    }

}
